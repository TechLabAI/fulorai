import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommIntegrationComponent } from './comm-integration.component';

describe('CommIntegrationComponent', () => {
  let component: CommIntegrationComponent;
  let fixture: ComponentFixture<CommIntegrationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommIntegrationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommIntegrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
