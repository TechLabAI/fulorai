import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommFeatureTemplateStudioComponent } from './comm-feature-template-studio.component';

describe('CommFeatureTemplateStudioComponent', () => {
  let component: CommFeatureTemplateStudioComponent;
  let fixture: ComponentFixture<CommFeatureTemplateStudioComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommFeatureTemplateStudioComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommFeatureTemplateStudioComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
