import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyFeatureJourneyListComponent } from './jrny-feature-journey-list.component';

describe('JrnyFeatureJourneyListComponent', () => {
  let component: JrnyFeatureJourneyListComponent;
  let fixture: ComponentFixture<JrnyFeatureJourneyListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyFeatureJourneyListComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyFeatureJourneyListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
