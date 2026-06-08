import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksFeatureRbacViewerComponent } from './wrks-feature-rbac-viewer.component';

describe('WrksFeatureRbacViewerComponent', () => {
  let component: WrksFeatureRbacViewerComponent;
  let fixture: ComponentFixture<WrksFeatureRbacViewerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksFeatureRbacViewerComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksFeatureRbacViewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
